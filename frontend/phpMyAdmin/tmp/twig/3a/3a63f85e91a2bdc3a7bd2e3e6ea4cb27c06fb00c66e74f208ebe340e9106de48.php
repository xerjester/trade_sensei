<?php

use Twig\Environment;
use Twig\Error\LoaderError;
use Twig\Error\RuntimeError;
use Twig\Extension\SandboxExtension;
use Twig\Markup;
use Twig\Sandbox\SecurityError;
use Twig\Sandbox\SecurityNotAllowedTagError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedFunctionError;
use Twig\Source;
use Twig\Template;

/* components/error_message.twig */
class __TwigTemplate_455a22b4684d3c6ddb476fa286ead2542077e190376955a4c4e01574de16e47c extends \Twig\Template
{
    private $source;
    private $macros = [];

    public function __construct(Environment $env)
    {
        parent::__construct($env);

        $this->source = $this->getSourceContext();

        $this->parent = false;

        $this->blocks = [
        ];
    }

    protected function doDisplay(array $context, array $blocks = [])
    {
        $macros = $this->macros;
        // line 1
        echo "<div class=\"alert alert-danger\" role=\"alert\">
    <img src=\"themes/dot.gif\" title=\"\" alt=\"\" class=\"icon ic_s_error\">
    ";
        // line 3
        echo twig_escape_filter($this->env, ($context["msg"] ?? null), "html", null, true);
        echo "
</div>
";
    }

    public function getTemplateName()
    {
        return "components/error_message.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  41 => 3,  37 => 1,);
    }

    public function getSourceContext()
    {
        return new Source("", "components/error_message.twig", "E:\\STUDENT\\phpMyAdmin\\templates\\components\\error_message.twig");
    }
}
